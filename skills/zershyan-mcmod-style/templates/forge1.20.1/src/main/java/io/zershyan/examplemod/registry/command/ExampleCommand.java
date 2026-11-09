package io.zershyan.examplemod.registry.command;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import net.minecraft.commands.CommandSourceStack;

import static net.minecraft.commands.Commands.argument;
import static net.minecraft.commands.Commands.literal;

public class ExampleCommand {
    public static void register(LiteralArgumentBuilder<CommandSourceStack> parent) {
        parent.then(literal("value")
                .then(argument("amount", IntegerArgumentType.integer(0))
                        .executes(context -> execute(
                                context.getSource(), IntegerArgumentType.getInteger(context, "amount")))));
    }

    private static int execute(CommandSourceStack source, int amount) {
        source.sendSuccess(() -> ExampleModKeyLang.CommandValueSet.get(amount), true);
        return amount;
    }
}
